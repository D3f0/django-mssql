select 'Running RegEx examples and tests.'

select 'Simple tests.'
select 
	dbo.REGEXP_LIKE('abc', 'abc', 1) as [Match case sensitive]
	, dbo.REGEXP_LIKE('abc', 'abc', 0) as [Match case insensitive]
	, dbo.REGEXP_LIKE('abc', 'ABC', 1) as [Match case sensitive]
	, dbo.REGEXP_LIKE('abc', 'ABC', 0) as [Doesn't match case insensitive]
