from typing import Union, Any
from fastapi import HTTPException, status

def check_user_id_authorization(user_id: Union[int, None], credentials_user_id: int) -> Union[HTTPException, None]:
    if (user_id) and (user_id != credentials_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to perform requested action.'
        )
    return


def check_object_availability(object: Any, msg: str, status_code: int) -> Union[HTTPException, None]:
    if not object:
        if status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
        )
        if status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg
            )
        if status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=msg
        )
    return


def check_resource_availability(resource: Any, msg: str, conflict: bool = False) -> Union[HTTPException, None]:
    
    if conflict:
        if resource:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=msg,
                )
    else:
        if resource:
            return resource
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg
            )


def check_uniqueness(unique: bool, unique_values: list, value: Any, msg: str,) -> Union[HTTPException, None]:
    if unique == True:
        if value in unique_values:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=msg,
                )#f'{field} not accepted.'
    
    if unique == False:
        if value not in unique_values:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg,
                )
    return
    

def check_password(validate_pw: callable) -> Union[HTTPException, None]:
    if not validate_pw:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'Invalid credentials'
        )
    return


def check_add_resource(add_resource: callable, status_code: int) -> Union[HTTPException, None]:
    """This function can be used to assess the successful resource addition or update."""
    
    try:
        add_resource()
    except Exception as e:
        if status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e), 
                )
        if status_code == 500: 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e), 
                )
        
    return

def check_delete_resource(to_delete: callable, msg: Any) -> Union[HTTPException, None]:
    try:
        to_delete()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg,
            )
    return


def check_partial_fields(input_fields: list, required_fields: list) -> Union[HTTPException, None]:
    if input_fields == required_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'To update all the fields make a PUT request.',
            )
    

