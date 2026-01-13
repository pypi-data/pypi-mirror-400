{attribute 'qualified_only'}
VAR_GLOBAL CONSTANT
    GC_VERSION : STRING := '1.0.0';
    GC_MAX_DEVICES : UINT := 64;
    GC_TIMEOUT_MS : TIME := T#5000MS;
    GC_PI : LREAL := 3.14159265358979;
END_VAR

VAR_GLOBAL
    g_bSystemReady : BOOL;
    g_nActiveDevices : UINT;
END_VAR

VAR_GLOBAL RETAIN
    g_nTotalCycles : ULINT;
    g_dtLastRun : DT;
END_VAR
