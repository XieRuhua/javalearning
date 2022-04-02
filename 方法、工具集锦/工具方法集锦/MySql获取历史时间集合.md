> **该方法主要用作统计数据填充（列举所有目标日期，匹配统计数据时填充不存在的日期的对应数据）**

```sql
SELECT
	@s := @s + 1 AS num,
	DATE_FORMAT( SUBDATE( NOW(), INTERVAL @s DAY ), '%Y-%m-%d' ) AS date_str	
FROM
	information_schema.`TABLES`,
	( SELECT @s := -1 ) temp 
WHERE
	@s < 6
```

执行结果（测试执行日期为：`2022/3/16`）：
| num  | date_str  |
| ---- | --------- |
| 0    | 2022/3/16 |
| 1    | 2022/3/15 |
| 2    | 2022/3/14 |
| 3    | 2022/3/13 |
| 4    | 2022/3/12 |
| 5    | 2022/3/11 |
| 6    | 2022/3/10 |

<font color="red">**注意：将其中 `-1` 改为 `0` 则是从昨天（`2022/3/15`）开始，且只查询历史`6`天; 需要同步将 `6` 改为目标历史天数**
</font>

该方法也可扩展为历史多少分钟的形式：
```sql
SELECT
	@s := @s + 1 AS num,
	DATE_FORMAT( SUBDATE( NOW(), INTERVAL @s MINUTE ), '%Y-%m-%d %H:%i' ) AS time_str
```
gantt
dateFormat YYYY-MM-DD
section S1
T1: 2014-01-01, 9d
section S2
T2: 2014-01-11, 9d
section S3
T3: 2014-01-02, 9d
```
	
FROM
	information_schema.`TABLES`,
	( SELECT @s := -1 ) temp 
WHERE
	@s < 6 
```
执行结果（测试执行时间为：`2022-03-16 16:57`）：
| num  | time_str         |
| ---- | ---------------- |
| 0    | 2022-03-16 16:57 |
| 1    | 2022-03-16 16:56 |
| 2    | 2022-03-16 16:55 |
| 3    | 2022-03-16 16:54 |
| 4    | 2022-03-16 16:53 |
| 5    | 2022-03-16 16:52 |
