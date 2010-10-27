CREATE FUNCTION dbo.REGEXP_LIKE
(
	@input nvarchar(4000),
	@pattern nvarchar(4000),
	@caseSensitive int
)
RETURNS bit
AS
BEGIN
	DECLARE @hresult integer
	DECLARE @oRegexp integer
	DECLARE @objMatches integer
	DECLARE @objMatch integer
	DECLARE @count integer
	DECLARE @results bit
	
	EXEC @hresult = sp_OACreate 'VBScript.RegExp', @oRegexp OUTPUT
	IF @hresult <> 0 return -1;

	EXEC @hresult = sp_OASetProperty @oRegexp, 'Pattern', @pattern
	IF @hresult <> 0 return -1;

	EXEC @hresult = sp_OASetProperty @oRegexp, 'Global', false
	IF @hresult <> 0 return -1;

	IF @caseSensitive = 0 EXEC @hresult = sp_OASetProperty @oRegexp, 'IgnoreCase', 1
	IF @hresult <> 0 return -1;

	EXEC @hresult = sp_OAMethod @oRegexp, 'Test', @results OUTPUT, @input
	IF @hresult <> 0 return -1;

	EXEC @hresult = sp_OADestroy @oRegexp
	IF @hresult <> 0 return -1;

	RETURN @results
END
