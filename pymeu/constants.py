CHUNK_SIZE = 1984 # Number of bytes to transfer per messsage.
                  # Appeared to work up to 2000 but not tested extensively.

HELPER_VERSIONS = {
    '11.00.00',
    '12.00.00.414.73'
}

ME_VERSIONS = {
    '11.00.00.230',
    '11.00.25.230',
    '12.00.78.414'
}

PRODUCT_CODES = {
    '102',  #PanelView Plus 7
    '51'    #PanelView Plus 6
}

PRODUCT_TYPES = {
    '24'
}

CREATE_DIR_SUCCESS = 183 # 'b\xb7'

GET_UNK1_VALUES = {
    b'\x02\x00'
}

GET_UNK2_VALUES = {
    b'\x01\x60'
}

GET_UNK3_VALUES = {
    b'\x64\x00'
}