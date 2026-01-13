FUNCTION FC_Calculate : REAL
VAR_INPUT
    fA : REAL;
    fB : REAL;
    eOperation : INT;
END_VAR
VAR
    fResult : REAL;
END_VAR

CASE eOperation OF
    0:
        fResult := fA + fB;
    1:
        fResult := fA - fB;
    2:
        fResult := fA * fB;
    3:
        IF fB <> 0.0 THEN
            fResult := fA / fB;
        ELSE
            fResult := 0.0;
        END_IF
ELSE
    fResult := 0.0;
END_CASE

FC_Calculate := fResult;

END_FUNCTION
