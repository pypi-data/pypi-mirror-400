(* Simple derived node - always returns FAILURE *)
FUNCTION_BLOCK FB_AlwaysFailure EXTENDS FB_BaseNode

METHOD Tick : E_NodeStatus
    Tick := E_NodeStatus.FAILURE;
    eLastStatus := E_NodeStatus.FAILURE;
END_METHOD

END_FUNCTION_BLOCK
