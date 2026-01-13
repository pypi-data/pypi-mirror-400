INTERFACE I_TreeNode

    // Method: Tick - Main execution method
    METHOD Tick : E_NodeStatus
    END_METHOD

    // Method: Halt - Stop execution
    METHOD Halt
    END_METHOD

    // Method: Reset - Reset state
    METHOD Reset : BOOL
    END_METHOD

    // Method: GetPath - Get node path
    METHOD GetPath : STRING(255)
    END_METHOD

    // Method: GetNodeName - Get node name
    METHOD GetNodeName : STRING(50)
    END_METHOD

    // Method: SetParent - Set parent node
    METHOD SetParent
        VAR_INPUT
            ipParent : I_TreeNode;
        END_VAR
    END_METHOD

    // Method: GetProgress - Get progress value
    METHOD GetProgress : REAL
    END_METHOD

    // Error handling methods
    METHOD HasError : BOOL
    END_METHOD

    METHOD GetError : ST_Error
    END_METHOD

    METHOD ClearError
    END_METHOD

END_INTERFACE
