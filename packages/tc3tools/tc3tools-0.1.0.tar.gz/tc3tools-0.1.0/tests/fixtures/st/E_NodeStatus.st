{attribute 'qualified_only'}
{attribute 'strict'}
TYPE E_NodeStatus :
(
    IDLE := 0,
    RUNNING,
    SUCCESS,
    FAILURE
) := IDLE;
END_TYPE
