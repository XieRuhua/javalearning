先看一下**AOP-Before/After的JoinPoint**以及 **@Around的ProceedingJoinPoint**的区别与联系：
```java
// 只列举部分关键代码
public interface JoinPoint {
    String toString();                  //连接点所在位置的相关信息
    String toShortString();             //连接点所在位置的简短相关信息
    String toLongString();              //连接点所在位置的全部相关信息
    Object getThis();                   //返回AOP代理对象，也就是com.sun.proxy.$Proxy18
    Object getTarget();                 //返回目标对象，一般我们都需要它或者（也就是定义方法的接口或类，为什么会是接口呢？这主要是在目标对象本身是动态代理的情况下，例如Mapper。所以返回的是定义方法的对象如aoptest.daoimpl.GoodDaoImpl或com.b.base.BaseMapper<T, E, PK>）
    Object[] getArgs();                 //返回被通知方法参数列表
    Signature getSignature();           //返回当前连接点签名  其getName()方法返回方法的FQN，如void aoptest.dao.GoodDao.delete()或com.b.base.BaseMapper.insert(T)(需要注意的是，很多时候我们定义了子类继承父类的时候，我们希望拿到基于子类的FQN，这直接可拿不到，要依赖于AopUtils.getTargetClass(point.getTarget())获取原始代理对象，下面会详细讲解)
    SourceLocation getSourceLocation(); //返回连接点方法所在类文件中的位置
    String getKind();                   //连接点类型
    JoinPoint.StaticPart getStaticPart();//返回连接点静态部分

    // 静态部分的参数
    public interface StaticPart {
        Signature getSignature();           //返回当前连接点签名
        SourceLocation getSourceLocation(); //获得连接点的通知类型
        String getKind();                   //连接点类型
        int getId();                        //唯一标识
        String toString();                  //连接点所在位置的相关信息
        String toShortString();             //连接点所在位置的简短相关信息
        String toLongString();              //连接点所在位置的全部相关信息
    }
}
```
**ProceedingJoinPoint继承自JoinPoint**，在原有基础上又额外定义了几个接口方法
```java
public interface ProceedingJoinPoint extends JoinPoint {
    // 执行方法 ，返回执行的结果 因为 环绕通知 不像 @Before @After 能够区分出，切点方法执行的前后要执行的前后顺序，
    //因此使用 proceed（）来 区分 方法执行的前后
    void set$AroundClosure(AroundClosure var1);

    default void stack$AroundClosure(AroundClosure arc) {
        throw new UnsupportedOperationException();
    }

    //使用自己定义的 参数去Object[] var1 去执行方法
    Object proceed() throws Throwable;

    Object proceed(Object[] var1) throws Throwable;
}
```

本例主要是应用于swagger，使用swagger的注解来记录操作日志：
```java
/**
 * @Author XieRuhua
 * @Date: 2021/4/29 16:34
 * @Version: 1.0
 * <p>
 * 操作日志记录的AOP
 */
@Aspect
@Component
public class OperationLogAcpect {
    private static Logger logger = LoggerFactory.getLogger(OperationLogAcpect.class);

    // 放过的路径
    @Value("${login-pass-url}")
    private String passUrl;
    // 创建一个可缓存线程池，如果线程池长度超过处理需要，可灵活回收空闲线程，若无可回收，则新建线程
    ExecutorService cachedThreadPool = Executors.newCachedThreadPool();

    /**
     * 定义切入点，切入点为com.example.aop下的所有函数
     */
    @Pointcut("@annotation(io.swagger.annotations.ApiOperation)")
    public void apiOperation() {
    }

    /**
     * 前置通知：在连接点之前执行的通知
     *
     * @param joinPoint
     * @throws Throwable
     */
    @Before("apiOperation()")
    public void doBefore(JoinPoint joinPoint) throws Throwable {
    }
    
    /**
     * 环绕通知：在连接点前后执行的通知
     */
    @Around("apiOperation()")
    public Object doAround(ProceedingJoinPoint pjp) throws Throwable {
        Object ret = pjp.proceed();
        try {
            HttpServletRequest request = ((ServletRequestAttributes) RequestContextHolder.getRequestAttributes()).getRequest();
            // IP信息和用户信息不放在异步线程中，防止request为空
            String ip = IpUtil.getIPAddress(request);
            // 判断是否是非必须登录的请求
            SysLoginUserInfo loginUserInfo = null;
            if (passUrl != null && passUrl.indexOf(request.getRequestURI()) == -1 && request.getRequestURI().indexOf("logout") == -1) {// 不需要拦截的和登出页面不获取用户信息
                loginUserInfo = UserUtils.getLoginUserInfo(request);
            }
            String uid = loginUserInfo != null ? loginUserInfo.getId() : "";
            String uname = loginUserInfo != null ? loginUserInfo.getRealName() : "";

            // 日志异步入库
            cachedThreadPool.execute(() -> {
                Signature signature = pjp.getSignature();
                MethodSignature methodSignature = (MethodSignature) signature;
                Method targetMethod = methodSignature.getMethod();
                ApiOperation apiOperation = targetMethod.getAnnotation(ApiOperation.class);
//                    Api api = targetMethod.getDeclaringClass().getAnnotation(Api.class);
                RequestMapping requestMapping = targetMethod.getDeclaringClass().getAnnotation(RequestMapping.class);
                GetMapping getMapping = targetMethod.getAnnotation(GetMapping.class);
                PostMapping postMapping = targetMethod.getAnnotation(PostMapping.class);

                String content = "";
                String type = "";
                if (apiOperation != null) {
                    content = apiOperation.value();
                    type = apiOperation.notes();
                }
                // 模块
                String moduleUrl = requestMapping.value()[0];
                String moduleName = ModelConstants.models.get(moduleUrl.substring(0, moduleUrl.indexOf("-") + 1));

                // 请求全路径
                String url = "";
                if (getMapping != null) {
                    url = getMapping.value()[0];
                } else if (postMapping != null) {
                    url = postMapping.value()[0];
                }

                // 返回结果
                String resultStr = "";
                if (ret instanceof JsonResult) {
                    JsonResult result = (JsonResult) ret;
                    if (ReturnCodes.RETURN_SUCCEED_CODE == result.getCode()) {
                        resultStr = "成功";
                    } else {
                        resultStr = result.getMessage();
                    }
                }

                SysOperationLogMapper sysOperationLogMapper = (SysOperationLogMapper) SpringContextUtil.getBean("SysOperationLogMapper");
                SysOperationLog sysOperationLog = new SysOperationLog();
                sysOperationLog.setUrl(moduleUrl + url);
                sysOperationLog.setModule(moduleName);
                sysOperationLog.setType(type);
                sysOperationLog.setContent(content);
                sysOperationLog.setResult(resultStr);
                sysOperationLog.setClientIp(ip);
                sysOperationLog.setCreateUserId(uid);
                sysOperationLog.setCreateUserName(uname);
                sysOperationLogMapper.insert(sysOperationLog);
            });
        } catch (Exception e) {
            logger.error("save operation log error :", e.getMessage());
            if (e instanceof LoginException && ret instanceof JsonResult) {
                JsonResult result = (JsonResult) ret;
                result = JsonResult.buildResponse(ReturnCodes.USER_LOGIN_ERROR_CODE, e.getMessage(), null);
                return result;
            }
        }
        return ret;
    }
}
```