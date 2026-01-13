FUNCTION_BLOCK FB_Sample
VAR_INPUT
    bEnable : BOOL;
    nValue : INT;
END_VAR
VAR_OUTPUT
    bDone : BOOL;
    nResult : INT;
END_VAR
VAR
    _state : INT;
END_VAR

IF bEnable THEN
    _state := _state + 1;
    nResult := nValue * 2;
    bDone := TRUE;
ELSE
    bDone := FALSE;
END_IF
END_FUNCTION_BLOCK
