{attribute 'qualified_only'}
{attribute 'strict'}
FUNCTION_BLOCK FB_WithMethods
VAR_INPUT
    bExecute : BOOL;
END_VAR
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrorId : UDINT;
END_VAR
VAR
    _counter : INT;
    _initialized : BOOL;
END_VAR

(* Main implementation *)
IF bExecute AND NOT _initialized THEN
    Initialize();
END_IF

METHOD PUBLIC Initialize : BOOL
VAR_INPUT
    nStartValue : INT := 0;
END_VAR
VAR
    i : INT;
END_VAR
    FOR i := 0 TO 10 DO
        _counter := _counter + 1;
    END_FOR
    _initialized := TRUE;
    Initialize := TRUE;
END_METHOD

METHOD PRIVATE Reset
VAR
    temp : INT;
END_VAR
    _counter := 0;
    _initialized := FALSE;
END_METHOD

METHOD Calculate : REAL
VAR_INPUT
    fInput : REAL;
END_VAR
VAR_OUTPUT
    fOutput : REAL;
END_VAR
VAR
    fTemp : REAL;
END_VAR
    CASE _counter OF
        0:
            fTemp := 0.0;
        1..5:
            fTemp := fInput * 2.0;
        6, 7, 8:
            fTemp := fInput / 2.0;
    ELSE
        fTemp := fInput;
    END_CASE
    
    fOutput := fTemp;
    Calculate := fTemp;
END_METHOD

END_FUNCTION_BLOCK
