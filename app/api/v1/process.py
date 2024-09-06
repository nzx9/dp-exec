from pyspark import SparkConf, SparkContext, RDD

conf = SparkConf().setAppName("Exe").setMaster("local")
sc = SparkContext(conf=conf)


def process_large_data(data):
    rdd = sc.parallelize(data)
    
    # Aggregate the total quantity for each user
    result = rdd.map(lambda x: (x['user_id'], sum([i['quantity'] for i in x['items']]))).reduceByKey(lambda a, b: a + b).collect()
    
    return result

# Pagination using RDDs
def paginate_rdd_data(rdd: RDD, page: int, page_size: int):
    start = (page - 1) * page_size
    end = start + page_size
    return rdd.collect()[start:end]