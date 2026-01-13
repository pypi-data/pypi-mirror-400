PROGRAM PRG_Main
VAR
    fbSimple : FB_SimpleBlock;
    fbMethods : FB_WithMethods;
    bStart : BOOL;
    nCycleCount : UDINT;
END_VAR

nCycleCount := nCycleCount + 1;

fbSimple(
    bEnable := bStart,
    nValue := 42
);

IF fbSimple.bDone THEN
    fbMethods(bExecute := TRUE);
END_IF

END_PROGRAM
