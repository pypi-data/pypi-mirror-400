TYPE ST_NestedData :
STRUCT
    bFlag : BOOL;
    nCount : INT;
END_STRUCT
END_TYPE

TYPE ST_Data :
STRUCT
    nId : UDINT;
    sName : STRING(80);
    fValue : REAL;
    dtTimestamp : DT;
    aBuffer : ARRAY[0..255] OF BYTE;
    stNested : ST_NestedData;
END_STRUCT
END_TYPE
