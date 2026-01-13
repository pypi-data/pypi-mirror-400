{attribute 'reflection'}
{attribute 'hide_all_locals'}
FUNCTION_BLOCK FB_EdgeCases EXTENDS FB_Base IMPLEMENTS I_Device
VAR_INPUT
    {attribute 'OPC.UA.DA' := '1'}
    fSetpoint : REAL := 0.0;
    sDescription : STRING(255) := 'Default description';
END_VAR
VAR_OUTPUT
    {attribute 'OPC.UA.DA.Access' := '1'}
    fActualValue : REAL;
END_VAR
VAR CONSTANT
    C_MAX_VALUE : REAL := 100.0;
    C_MIN_VALUE : REAL := -100.0;
END_VAR
VAR
    // Single line comment
    _state : INT;
    (* Block comment *)
    _timer : TON;
    (*
        Multi-line
        block comment
    *)
    _lastValue : REAL;
END_VAR

// Edge case: IF-ELSIF-ELSE chain
IF fSetpoint > C_MAX_VALUE THEN
    fActualValue := C_MAX_VALUE;
ELSIF fSetpoint < C_MIN_VALUE THEN
    fActualValue := C_MIN_VALUE;
ELSIF fSetpoint = 0.0 THEN
    fActualValue := _lastValue;
ELSE
    fActualValue := fSetpoint;
END_IF

// Edge case: Nested IF
IF _state = 1 THEN
    IF fSetpoint > 0.0 THEN
        IF _timer.Q THEN
            fActualValue := fSetpoint;
        END_IF
    END_IF
END_IF

// Edge case: WHILE loop
WHILE _state = 0 DO
    _state := 1;
END_WHILE

// Edge case: REPEAT-UNTIL
REPEAT
    _lastValue := fActualValue;
UNTIL _state <> 1
END_REPEAT

_lastValue := fActualValue;

METHOD PUBLIC FB_init : BOOL
VAR_INPUT
    bInitRetains : BOOL;
    bInCopyCode : BOOL;
END_VAR
    _state := 0;
    FB_init := TRUE;
END_METHOD

{attribute 'TcRpcEnable'}
METHOD ProcessData : BOOL
VAR_INPUT
    nSize : UDINT;
END_VAR
VAR
    i : UDINT;
END_VAR
    FOR i := 0 TO nSize - 1 DO
        // Process each item
        _lastValue := _lastValue + 1.0;
    END_FOR
    ProcessData := TRUE;
END_METHOD

END_FUNCTION_BLOCK
