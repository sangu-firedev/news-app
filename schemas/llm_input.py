from pydantic import BaseModel, validator


class sub_article_check(BaseModel):

    title : str
    publisher : str
    topic : str
    published : str
    article : str 
