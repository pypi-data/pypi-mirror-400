*** Settings ***
Library    Relukko

Suite Setup    Set Up Relukko    ${BASE_URL}    ${API_KEY}


*** Variables ***
${BASE_URL}    set on run
${API_KEY}     set on run
${VER_STR}     set on run


*** Test Cases ***
Relukko Life Cycle
    ${lock}    Acquire Relukko    Rf Lock    30s
    Log    ${lock}
    ${lock}    Keep Relukko Alive For The Next    6m
    Log    ${lock}
    ${lock}    Keep Relukko Alive For The Next "50" Seconds
    Log    ${lock}
    ${lock}    Keep Relukko Alive For The Next 5 Min
    Log    ${lock}
    ${lock}    Add To Current Relukko Expire At Time    7m
    Log    ${lock}
    ${lock}    Add To Current Relukko Expire At Time "60" Seconds
    Log    ${lock}
    ${lock}    Add To Current Relukko Expire At Time 5 Min
    Log    ${lock}
    ${lock}    Update Relukko    creator=Mark
    Log    ${lock}
    ${lock}    Update Relukko    expires_at=2025-01-01T12:34:56.123456Z
    Log    ${lock}
    ${lock}    Get Current Relukko
    Log    ${lock}
    ${expires_at}    Get Relukko Expires At Time
    Log    ${expires_at}
    ${created_at}    Get Relukko Created At Time
    Log    ${created_at}
    ${lock}    Get All Relukkos
    Log    ${lock}
    ${lock}    Delete Relukko
    Log    ${lock}

Aquire Lock From Tags
    [Tags]    test_case_id:4be49c5a-ca80-43f8-8144-36a3b1aae24e
    ${lock}    Acquire Relukko For Test
    Log    ${lock}
    Should Be Equal    ${lock}[lock_name]    4be49c5a-ca80-43f8-8144-36a3b1aae24e
    ${lock}    Delete Relukko
    Log    ${lock}

Aquire Lock For Test
    ${lock}    Acquire Relukko For Test
    Log    ${lock}
    Should Be Equal    ${lock}[lock_name]    Relukko-${VER_STR}:Aquire Lock For Test
    ${lock}    Delete Relukko
    Log    ${lock}
