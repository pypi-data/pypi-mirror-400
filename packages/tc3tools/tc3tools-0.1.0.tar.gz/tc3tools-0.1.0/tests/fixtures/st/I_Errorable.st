INTERFACE I_Errorable

    METHOD HasError : BOOL
    END_METHOD

    METHOD GetError : ST_Error
    END_METHOD

    METHOD ClearError
    END_METHOD

END_INTERFACE
