
from tpf.data.utils import ReadDeal as rd 
from tpf.data.utils import GroupDeal as gd


class DataDeal:
    def __init__(self):
        pass
    
    @classmethod
    def data_split(cls, X, y, test_size=0.2, random_state=None):
        from tpf.d1 import DataDeal as dtold
        df = dtold.data_split(X, y, test_size=test_size, random_state=random_state)
        return df  
    
    @classmethod
    def read_csv(cls,data_path, 
                    use_cols=[], 
                    to_col2=[], 
                    log_path=None):
        """
        - 读取csv，支持gbk,utf-8，
        - 可以读取的时候，选择列，并进行列的转换
        """
        df = rd.text2Xy(
            data_path=data_path, 
            use_cols=use_cols, 
            to_col2=to_col2, 
            log_path=log_path )
    
        return df  
    
    @classmethod
    def label_merge(cls, data_path, 
                    form_col1, to_col2, 
                    need_merge_cols = [],
                    label_new_name='label',
                    lable_padding="lable_padding", 
                    label_null_flag='', 
                    label_split_flag = '-',
                    log_path=None,):
        """
        - 针对text多标签的情况，对标签进行合并，合并的过程中去除空格，对齐
        - label_null_flag:如果某级标签为None，则进行替换
        - label_split_flag:多级标签分隔符
        """
        df = rd.text2Xy(data_path=data_path, 
                   use_cols=form_col1, 
                   to_col2=to_col2, 
                   need_merge_cols = need_merge_cols,
                   label_new_name=label_new_name,
                   lable_padding=lable_padding, 
                   log_path=log_path,
                   null_flag=label_null_flag, split_flag = label_split_flag)
    
        return df  
    
    @classmethod
    def label_score_transform(cls, 
                    df,
                    group_key='label',
                    score_col='score',
                    transform_type='mean',
                    score_col_new=None):
        """
        - transform_type (str): 统计变换类型，默认为'mean'
            可选值：
            - 'mean': 平均值
            - 'sum': 求和
            - 'count': 计数
            - 'std': 标准差
            - 'var': 方差
            - 'min': 最小值
            - 'max': 最大值
            - 'median': 中位数
            - 'first': 第一个值
            - 'last': 最后一个值
            - 'zscore': z-score分数, 异常检测, 通常 |z| > 3 的值可视为异常值 
        """
        result = gd.label_score_transform(
            df,
            group_key=group_key,
            score_col=score_col,
            transform_type=transform_type,
            score_col_new=score_col_new
        )
        return result 

    @classmethod
    def topk_label_mean(cls,df,
            group_key='label',
            score_col='score',
            top_k=5,
            score_col_new='mean_score',
            keep_name='text'):

        # 计算每个标签前k个高分样本的均值分数
        result = gd.topk_label_score_mean(
            df,
            group_key=group_key,
            score_col=score_col,
            top_k=top_k,
            score_col_new=score_col_new,
            keep_name=keep_name
        )
        return result





