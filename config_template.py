# **** 文件地址配置 **** #
log_path = "./log/"
old_database_path_v0210 = ""
new_database_path_v0171 = ""
new_database_schema_path_v0171 = "./assets/memos_0171_struct.sql"

# **** 用户配置 **** #
creator_id = 1  # 暂时只支持一个用户的操作

# **** 标签配置 **** #
tags_dict = {  # 暂不支持三级标签
    "Tag1": {
        "Tag1-1": "#Tag1/Tag1-1 ",
        "Tag1-2": "#Tag1/Tag1-2 ",
        "Tag1-3": "#Tag1/Tag1-3 ",
    },
    "Tag2": {
        "Tag2-1": "#Tag2/Tag2-1 ",
        "Tag2-2": "#Tag2/Tag2-2 ",
        "Tag2-3": "#Tag2/Tag2-3 ",
    },
    "Tag3": "#Tag3 ",
    "Tag4": "#Tag4 ",
}
