CHUNK_SIZE = 1984 # Number of bytes to transfer per messsage.
                  # Appeared to work up to 2000 but not tested extensively.

HELPER_VERSIONS = {
    '5.10.00',
    '7.00.00',
    '8.00.00',
    '8.10.00',
    '8.20.00',
    '9.00.00',
    '10.00.00',
    '11.00.00',
    '12.00.00',
    '12.00.00.414.73',
    '13.00.00'
}

ME_VERSIONS = {
    '5.10.16.09',
    '7.00.20.13',
    '7.00.55.13',
    '8.00.67.12',
    '8.10.42.13',
    '8.20.30.10',
    '9.00.17.241',
    '9.00.00.241',
    '10.00.09.290',
    '11.00.00.230',
    '11.00.25.230',
    '12.00.00.414',
    '12.00.78.414',
    '13.00.11.413'
}

PRODUCT_CODES = {
    '17',   #PanelView Plus
    '47',   #PanelView Plus 6 1000
    '48',   #PanelView Plus 6
    '51',   #PanelView Plus 6
    '94',   #PanelView Plus 7 700 Perf
    '98',   #PanelView Plus 7 1000 Perf
    '102',  #PanelView Plus 7
    '187',  #PanelView Plus 7 1000 Standard
    '189'   #PanelView Plus 7 1200 Standard
}

PRODUCT_TYPES = {
    '24'
}

CREATE_DIR_SUCCESS = 183 # 'b\xb7'

GET_UNK1_VALUES = {
    b'\x02\x00'
}

GET_UNK2_VALUES = {
    b'\x01\x60',
    b'\x03\x41'
}

GET_UNK3_VALUES = {
    b'\x64\x00'
}