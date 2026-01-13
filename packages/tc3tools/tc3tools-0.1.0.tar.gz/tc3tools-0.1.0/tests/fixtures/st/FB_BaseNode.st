{attribute 'qualified_only'}
FUNCTION_BLOCK FB_BaseNode IMPLEMENTS I_TreeNode, I_Errorable
VAR
    eLastStatus : E_NodeStatus := E_NodeStatus.IDLE;
    _sNodeName : STRING(50);
    rProgress : REAL := 0.0;
    _fbErrorHandler : FB_ErrorHandler;
    _sFailedChildName : STRING(50);
    _ipParent : I_TreeNode;
    _bHalted : BOOL := FALSE;
END_VAR

PROPERTY NodeName : STRING(50)
    GET
    NodeName := _sNodeName;
    END_GET
    SET
    _sNodeName := NodeName;
    _fbErrorHandler.Initialize(_sNodeName);
    END_SET
END_PROPERTY

METHOD Tick : E_NodeStatus
    Tick := E_NodeStatus.IDLE;
END_METHOD

METHOD Halt
    _bHalted := TRUE;
    eLastStatus := E_NodeStatus.IDLE;
    rProgress := 0.0;
END_METHOD

METHOD Reset : BOOL
    _bHalted := FALSE;
    eLastStatus := E_NodeStatus.IDLE;
    rProgress := 0.0;
    ClearError();
    Reset := TRUE;
END_METHOD

METHOD PUBLIC SetParent
    VAR_INPUT
        ipParent : I_TreeNode;
    END_VAR
    _ipParent := ipParent;
END_METHOD

METHOD PUBLIC GetPath : STRING(255)
    VAR
        sPath : STRING(255);
    END_VAR
    IF _ipParent <> 0 THEN
        sPath := _ipParent.GetPath();
        IF LEN(sPath) > 0 THEN
            sPath := CONCAT(sPath, '/');
        END_IF
        sPath := CONCAT(sPath, _sNodeName);
    ELSE
        sPath := _sNodeName;
    END_IF
    GetPath := sPath;
END_METHOD

METHOD PUBLIC GetNodeName : STRING(50)
    GetNodeName := _sNodeName;
END_METHOD

METHOD PUBLIC SetError
    VAR_INPUT
        eErrorId : E_ErrorId;
        sMessage : STRING(255);
    END_VAR
    _fbErrorHandler.Raise(eErrorId, sMessage);
END_METHOD

METHOD PUBLIC HasError : BOOL
    HasError := _fbErrorHandler.IsActive();
END_METHOD

METHOD PUBLIC GetError : ST_Error
    GetError := _fbErrorHandler.GetError();
END_METHOD

METHOD PUBLIC ClearError
    _fbErrorHandler.Clear();
    _sFailedChildName := '';
END_METHOD

METHOD PUBLIC GetProgress : REAL
    GetProgress := rProgress;
END_METHOD

METHOD PROTECTED UpdateProgress
    VAR_INPUT
        nCurrent : INT;
        nTotal : INT;
    END_VAR
    IF nTotal > 0 THEN
        rProgress := (INT_TO_REAL(nCurrent) / INT_TO_REAL(nTotal)) * 100.0;
    ELSE
        rProgress := 0.0;
    END_IF
END_METHOD

METHOD PROTECTED SetProgressComplete
    rProgress := 100.0;
END_METHOD

END_FUNCTION_BLOCK
