using System;
using System.Data.SqlTypes;
using System.Text.RegularExpressions;
using Microsoft.SqlServer.Server;

public partial class UserDefinedFunctions
{
	private const RegexOptions DefaultRegExOptions =
		RegexOptions.IgnorePatternWhitespace | RegexOptions.Singleline;

	[SqlFunction(IsDeterministic = true, IsPrecise = true)]
	public static SqlInt32 REGEXP_LIKE(SqlString input, SqlString pattern, SqlInt32 caseSensitive)
	{
		RegexOptions options = DefaultRegExOptions;
		if (caseSensitive==0)
			options |= RegexOptions.IgnoreCase;

		return Regex.IsMatch(input.Value, pattern.Value, options) ? 1 : 0;
	}
}