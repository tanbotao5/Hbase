client = Hbase.Client(protocol)
数据类型定义：
ColumnDescriptor:
struct ColumnDescriptor {
  1:Text name,
  2:i32 maxVersions = 3,
  3:string compression = "NONE",
  4:bool inMemory = 0,
  5:string bloomFilterType = "NONE",
  6:i32 bloomFilterVectorSize = 0,
  7:i32 bloomFilterNbHashes = 0,
  8:bool blockCacheEnabled = 0,
  9:i32 timeToLive = -1
}

TRegionInfo：
struct TRegionInfo {
  1:Text startKey,
  2:Text endKey,
  3:i64 id,
  4:Text name,
  5:byte version,
  6:Text serverName,
  7:i32 port
}
Mutation：
struct Mutation {
  1:bool isDelete = 0,
  2:Text column,
  3:Text value,
  4:bool writeToWAL = 1
}

TRowResult：
struct TRowResult {
  1:Text row,
  2:map<Text, TCell> columns
}


#获取所有表名，返回list
client.getTablesNames()
#使能表        返回true  false
client.enableTable('table')
#不使能表
client.disableTable（‘table’）
#判断表是否使能  返回true  false
client.isTableEnabled('table')
#暂定，不清楚
client.compact(self, tableNameOrRegionName)
client.majorCompact(self, tableNameOrRegionName)
#获取表列族信息,返回字典
client.getColumnDescriptors('table')
# List the regions associated with a table  返回list
client.getTableRegions（‘table’）
#建立表‘table’及表中列族data。
data = ColumnDescriptor(name = 'test')
client.createTable('table',[data,])
#删除表，删除之前需要 disableTable
client.deleteTable('table')

#数据cell获取  返回list[TCell类]。提取数据用p[0].__dict__
p = client.get('table', ‘rowkey', 'column:name'/ 'column', 'attributes'=None)
#检索条件多加一个version号
client.getVer(self, tableName, row, column, numVersions, attributes)
##检索条件多加一个timestamp
client.getVerTs(tableName, row, column, timestamp=1446708556096, numVersions =2, attributes=None)
#获取一行所有信息，p[0]__dict__提取信息
p = client.getRow(tableName, row, attributes=None)
# 指定行列获取一行所有信息，p[0]__dict__提取信息.
p = client.getRowWithColumns(tableName, row, 'columns:name',attributes=None)
# 指定行列获取一行所有信息，p[0]__dict__提取信息.
#返回示例   {'sorted':None,'columns':{'column':TCell(timestamp=12345667,value='1234')},'row':'2'}
p = client.getRowTs( tableName, row, timestamp, attributes=None)

# 指定行列获取一行所有信息，p[0]__dict__提取信息.
#返回示例   {'sorted':None,'columns':{'column':TCell(timestamp=12345667,value='1234')},'row':'2'}
p = client.getRowWithColumnsTs(self, tableName, row, [columns:name,、、、], timestamp, attributes=None)

#获取行数据  数据类型   TRowResult  p[0]__dict__提取信息.
client.getRows( tableName, [rows,], attributes).
#获取行数据  数据类型TRowResult  p[0]__dict__提取信息. 匹配检索的列族
p = client.getRowsWithColumns( tableName, [row,], ['column:name'], attributes=None)

#获取行数据  数据类型TRowResult  p[0]__dict__提取信息. 匹配检索的列族,多个时间戮约束
p = client.getRowsWithColumnsTs( ‘tableName’, [row,],[ 'column:name',], timestamp, attributes=None)

#注意。只能是对某行的列族数据的更新或者删除操作，是创建列族的操作，如果新建行，可以做为创建列族详情见Mutation结构定义
mu = [Mutation(isDelete=1,column='column:name',value="1233"),]
p = client.mutateRow( 'tableName', row, mutations=mu, attributes=None)

#注意。只能是对某行的列族数据的更新或者删除操作，是创建列族的操作，如果新建行，可以做为创建列族详情见Mutation结构定义，
#多加一个时间戮，删除做为约束条件，添加数据这个参数无意义
mu = [Mutation(isDelete=1,column='column:name',value="1233"),]
p = client.mutateRowTs( 'tableName', row, mutations=mu, timestamp=24234, attributes = None)
#暂定 不清楚 rowBatches参数
client.mutateRows(self, tableName, rowBatches, attributes):
#暂定
client.mutateRowsTs(self, tableName, rowBatches, timestamp, attributes)
# Atomically increment the column value specified.  Returns the next value post increment.
#对列族中字段值相加，可以做为计数器使用
client.atomicIncrement( tableName, row, column, value)
#删除对应的单元格数据值，不删除列族字段
client.deleteAll('tableName', 'row', 'column:name', attributes=None)
#删除对应的单元格数据值，不删除列族字段,多加一个时间戮约束,时间戳是等于或大于过去的时间戳。
client.deleteAllTs(self, tableName, row, column, timestamp, attributes)
#删除对应行所有数据
client.deleteAllRow( 'tableName', 'row', attributes =None)
#删除对应行所有数据，时间戳是等于或大于过去的时间戳即可删除。
client.deleteAllRowTs('tableName', 'row', timestamp=123312, attributes=None)

#返回多行则需要使用scan
scan = TScan()
TScan的属性(检索条件如下)
startRow:
stopRow:
timestamp:
columns:
caching:
filterString: filter
sortColumns:
filter有如下条件：
#限制某个列的值等于26
filter = "ValueFilter(=,'binary:26')"
#值包含6这个值
filter = "ValueFilter(=,'substring:6')"
#列名中的前缀为birthday的
filter = "ColumnPrefixFilter('birth')"
#支持多个过滤条件通过括号、AND和OR的条件组合
filter = "ColumnPrefixFilter('birth') AND ValueFilter ValueFilter(=,'substring:1987')"
#对Rowkey的前缀进行判断
filter = "PrefixFilter('E')"
scan.filterString = "ValueFilter(=,'substring:6')"  #
id = client.scannerOpenWithScan(tableName, scan, None)
#返回10行
result2 = client.scannerGetList(id, 10)
#scannerGet则是每次只取一行数据
result = client.scannerGet(id)

#"不知道row的情况下访问hbase,获取所有的row"
scanner = client.scannerOpen(table,startRow, columns,None)
scannerclient.scannerOpenTs(tableName, startRow, columns, timestamp, attributes=None)                       #多加一个时间戮参数
scannerclient.scannerOpenWithStopTs(self, tableName, startRow, stopRow, columns, timestamp, attributes=None)#多加一个stopRow
r = self.client.scannerGet(scanner)
while r :
      r = self.client.scannerGet(scanner)
      self.client.scannerClose(scanner)
client.scannerClose(self, id)
