(* Action node that extends base node *)
FUNCTION_BLOCK FB_ActionNode EXTENDS FB_BaseNode
VAR
    _nExecutionCount : INT;
    _bFirstExecution : BOOL := TRUE;
END_VAR

METHOD Tick : E_NodeStatus
    IF _bFirstExecution THEN
        _bFirstExecution := FALSE;
        _nExecutionCount := 0;
    END_IF
    
    _nExecutionCount := _nExecutionCount + 1;
    
    IF HasError() THEN
        Tick := E_NodeStatus.FAILURE;
    ELSE
        Tick := E_NodeStatus.SUCCESS;
    END_IF
    
    eLastStatus := Tick;
END_METHOD

METHOD Reset : BOOL
    SUPER^.Reset();
    _nExecutionCount := 0;
    _bFirstExecution := TRUE;
    Reset := TRUE;
END_METHOD

METHOD PUBLIC GetExecutionCount : INT
    GetExecutionCount := _nExecutionCount;
END_METHOD

END_FUNCTION_BLOCK
