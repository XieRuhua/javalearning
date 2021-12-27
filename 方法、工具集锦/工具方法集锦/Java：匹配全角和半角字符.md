```java
import org.apache.commons.lang.StringUtils;

/**
 * @Author XieRuhua
 * @Date: 2021/7/16 16:19
 * @Version: 1.0
 * <p>
 * 匹配全角和半角字符（忽略大小写）
 */
public class EqualsDBCUtil {
    public static void main(String[] args) {
        String a = "123aBc";
        String b = "123ａbｃ";
        System.out.println(equalsDBC(a, b));
    }

    public static Boolean equalsDBC(String str1, String str2) {
        // 都为空则为true
        if (StringUtils.isBlank(str1) && StringUtils.isBlank(str2)) {
            return true;
        }
        if ((StringUtils.isBlank(str1) && StringUtils.isNotBlank(str2)) || (StringUtils.isNotBlank(str1) && StringUtils.isBlank(str2))) {
            return false;
        }

        // 全部转半角在转大写之后匹配
        return toDBC(str1).toUpperCase().equals(toDBC(str2).toUpperCase());
    }

    /**
     * 转半角的函数(DBC case)<br/><br/>
     * 全角空格为12288，半角空格为32
     * 其他字符半角(33-126)与全角(65281-65374)的对应关系是：均相差65248
     *
     * @param input 任意字符串
     * @return 半角字符串
     */
    public static String toDBC(String input) {
        char[] c = input.toCharArray();
        for (int i = 0; i < c.length; i++) {
            if (c[i] == 12288) {
                //全角空格为12288，半角空格为32
                c[i] = (char) 32;
                continue;
            }
            if (c[i] > 65280 && c[i] < 65375)
                //其他字符半角(33-126)与全角(65281-65374)的对应关系是：均相差65248
                c[i] = (char) (c[i] - 65248);
        }
        return new String(c);
    }
}
```
