(* Simple derived node - always returns SUCCESS *)
FUNCTION_BLOCK FB_AlwaysSuccess EXTENDS FB_BaseNode

METHOD Tick : E_NodeStatus
    Tick := E_NodeStatus.SUCCESS;
    eLastStatus := E_NodeStatus.SUCCESS;
    SetProgressComplete();
END_METHOD

END_FUNCTION_BLOCK
