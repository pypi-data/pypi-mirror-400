{attribute 'qualified_only'}
{attribute 'strict'}
(* Condition node with EXTENDS and multiple interface check *)
FUNCTION_BLOCK FB_ConditionNode EXTENDS FB_BaseNode
VAR_INPUT
    bCondition : BOOL;
END_VAR
VAR
    _bLastCondition : BOOL;
    _nEvaluationCount : UDINT;
END_VAR

METHOD Tick : E_NodeStatus
    _nEvaluationCount := _nEvaluationCount + 1;
    _bLastCondition := bCondition;
    
    IF bCondition THEN
        Tick := E_NodeStatus.SUCCESS;
        SetProgressComplete();
    ELSE
        Tick := E_NodeStatus.FAILURE;
    END_IF
    
    eLastStatus := Tick;
END_METHOD

METHOD Reset : BOOL
    SUPER^.Reset();
    _bLastCondition := FALSE;
    _nEvaluationCount := 0;
    Reset := TRUE;
END_METHOD

PROPERTY EvaluationCount : UDINT
    GET
    EvaluationCount := _nEvaluationCount;
    END_GET
END_PROPERTY

PROPERTY LastCondition : BOOL
    GET
    LastCondition := _bLastCondition;
    END_GET
END_PROPERTY

END_FUNCTION_BLOCK
