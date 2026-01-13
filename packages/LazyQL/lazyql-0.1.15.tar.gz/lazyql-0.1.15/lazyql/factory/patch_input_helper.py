from typing import (
    List,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import strawberry
from pydantic import BaseModel

# Cache global pour stocker les types Input enregistrés
_REGISTERED_INPUT_TYPES = {}


def register_input_type(model: Type[BaseModel], input_type: Type):
    """Enregistre un type Input pour un modèle Pydantic."""
    _REGISTERED_INPUT_TYPES[model.__name__] = input_type


def get_registered_input_type(model_name: str):
    """Récupère un type Input enregistré."""
    return _REGISTERED_INPUT_TYPES.get(model_name)


def create_patch_input_type(model: Type[BaseModel], name: str):
    """
    Crée un type d'entrée partiel (Patch) directement comme type Strawberry,
    sans passer par le décorateur Pydantic pour éviter les doublons.
    """
    # Récupérer les champs du modèle
    try:
        type_hints = get_type_hints(model)
    except Exception:
        type_hints = {k: v.annotation for k, v in model.model_fields.items()}

    # Construire un dictionnaire de fields Strawberry
    field_dict = {}
    annotations = {}

    for field_name, field_type in type_hints.items():
        if field_name in ["id", "_id"]:
            continue

        # Traiter le type pour utiliser les Input enregistrés
        processed_type = _process_field_type(field_type)

        # Rendre Optional
        if not _is_optional(processed_type):
            final_type = Optional[processed_type]
        else:
            final_type = processed_type

        annotations[field_name] = final_type
        field_dict[field_name] = strawberry.field(default=strawberry.UNSET)

    def to_pydantic(self_obj):
        return {
            k: v
            for k, v in vars(self_obj).items()
            if v is not strawberry.UNSET and not k.startswith("_")
        }

    # Créer la classe dynamiquement
    field_dict["__annotations__"] = annotations
    field_dict["__module__"] = model.__module__
    field_dict["to_pydantic"] = to_pydantic

    patch_class = type(f"{name}PatchInput", (), field_dict)

    # Décorer avec strawberry.input (pas pydantic.input)
    return strawberry.input(patch_class, name=f"{name}PatchInput")


def _process_field_type(field_type: Type) -> Type:
    """
    Traite récursivement les types pour remplacer les modèles Pydantic
    par leurs Input Strawberry enregistrés.
    """
    origin = get_origin(field_type)

    # Gérer Optional[X]
    if origin is Union:
        args = get_args(field_type)
        if type(None) in args:
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                processed = _process_field_type(non_none_args[0])
                return Optional[processed]

    # Gérer List[X]
    if origin is list or origin is List:
        args = get_args(field_type)
        if args:
            processed = _process_field_type(args[0])
            return List[processed]

    # Remplacer les modèles Pydantic par leurs Input Strawberry
    if isinstance(field_type, type) and issubclass(field_type, BaseModel):
        registered = get_registered_input_type(field_type.__name__)
        if registered:
            return registered

    # Type primitif
    return field_type


def _is_optional(field_type: Type) -> bool:
    """Vérifie si un type est Optional."""
    origin = get_origin(field_type)
    if origin is Union:
        args = get_args(field_type)
        return type(None) in args
    return False
