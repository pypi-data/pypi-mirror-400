{attribute 'qualified_only'}
{attribute 'strict'}
TYPE E_Status :
(
    Idle := 0,
    Initializing,
    Running,
    Paused,
    Stopping,
    Error := 99
) := Idle;
END_TYPE
