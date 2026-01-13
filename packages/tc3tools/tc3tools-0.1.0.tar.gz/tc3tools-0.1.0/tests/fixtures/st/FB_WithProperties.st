FUNCTION_BLOCK FB_WithProperties
VAR
    _value : INT;
    _name : STRING(80);
    _enabled : BOOL;
END_VAR

PROPERTY PUBLIC Value : INT
GET
VAR
    temp : INT;
END_VAR
    temp := _value;
    Value := temp;
END_GET
SET
    _value := Value;
END_SET
END_PROPERTY

PROPERTY Name : STRING(80)
GET
    Name := _name;
END_GET
SET
    _name := Name;
END_SET
END_PROPERTY

PROPERTY Enabled : BOOL
GET
    Enabled := _enabled;
END_GET
END_PROPERTY

METHOD DoWork : BOOL
    IF _enabled THEN
        _value := _value + 1;
        DoWork := TRUE;
    END_IF
END_METHOD

END_FUNCTION_BLOCK
