引入依赖：
```xml
<!-- 
    阿里excel导入导出 
    官方使用说明：https://www.yuque.com/easyexcel
-->
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>easyexcel</artifactId>
    <version>2.2.5</version>
</dependency>
<!-- Apache流处理工具包 -->
<dependency>
    <groupId>commons-io</groupId>
    <artifactId>commons-io</artifactId>
    <version>2.4</version>
</dependency>
```
创建一个工具类 ZipUtil:  
该工具类提供压文件夹压缩，文件压缩，压缩包解压缩。
```java

import java.io.*;
import java.util.Enumeration;
import java.util.zip.*;

public class ZipUtil {
    static final int BUFFER = 8192;

    public static void compress(String srcPath, String dstPath) throws IOException {
        File srcFile = new File(srcPath);
        File dstFile = new File(dstPath);
        if (!srcFile.exists()) {
            throw new FileNotFoundException(srcPath + "不存在！");
        }

        FileOutputStream out = null;
        ZipOutputStream zipOut = null;
        try {
            out = new FileOutputStream(dstFile);
            CheckedOutputStream cos = new CheckedOutputStream(out, new CRC32());
            zipOut = new ZipOutputStream(cos);
            String baseDir = "";
            compress(srcFile, zipOut, baseDir);
        } finally {
            if (null != zipOut) {
                zipOut.close();
                out = null;

                //压缩成功后，删除打包前的文件
                deleteFile(new File(srcPath));
            }

            if (null != out) {
                out.close();
            }
        }
    }

    private static void compress(File file, ZipOutputStream zipOut, String baseDir) throws IOException {
        if (file.isDirectory()) {
            compressDirectory(file, zipOut, baseDir);
        } else {
            compressFile(file, zipOut, baseDir);
        }
    }

    /**
     * 压缩一个目录
     */
    private static void compressDirectory(File dir, ZipOutputStream zipOut, String baseDir) throws IOException {
        File[] files = dir.listFiles();
        for (int i = 0; i < files.length; i++) {
            compress(files[i], zipOut, baseDir + dir.getName() + "/");
        }
    }

    /**
     * 压缩一个文件
     */
    private static void compressFile(File file, ZipOutputStream zipOut, String baseDir) throws IOException {
        if (!file.exists()) {
            return;
        }

        BufferedInputStream bis = null;
        try {
            bis = new BufferedInputStream(new FileInputStream(file));
            ZipEntry entry = new ZipEntry(baseDir + file.getName());
            zipOut.putNextEntry(entry);
            int count;
            byte data[] = new byte[BUFFER];
            while ((count = bis.read(data, 0, BUFFER)) != -1) {
                zipOut.write(data, 0, count);
            }

        } finally {
            if (null != bis) {
                bis.close();
            }
        }
    }

    /**
     * 将Zip文件解压缩到目标目录
     *
     * @param zipFile 压缩包文件地址
     * @param dstPath 解压缩文件目标地址
     * @throws IOException
     */
    public static void decompress(String zipFile, String dstPath) throws IOException {
        File pathFile = new File(dstPath);
        if (!pathFile.exists()) {
            pathFile.mkdirs();
        }
        ZipFile zip = new ZipFile(zipFile);
        for (Enumeration entries = zip.entries(); entries.hasMoreElements(); ) {
            ZipEntry entry = (ZipEntry) entries.nextElement();
            String zipEntryName = entry.getName();
            InputStream in = null;
            OutputStream out = null;
            try {
                in = zip.getInputStream(entry);
                String outPath = (dstPath + "/" + zipEntryName).replaceAll("\\*", "/");
                ;
                //判断路径是否存在,不存在则创建文件路径
                File file = new File(outPath.substring(0, outPath.lastIndexOf('/')));
                if (!file.exists()) {
                    file.mkdirs();
                }
                //判断文件全路径是否为文件夹,如果是上面已经上传,不需要解压
                if (new File(outPath).isDirectory()) {
                    continue;
                }

                out = new FileOutputStream(outPath);
                byte[] buf1 = new byte[1024];
                int len;
                while ((len = in.read(buf1)) > 0) {
                    out.write(buf1, 0, len);
                }
            } finally {
                if (null != in) {
                    in.close();
                }

                if (null != out) {
                    out.close();
                }
            }
        }
        zip.close();
    }

    /**
     * 删除文件夹
     * 用于删除临时组装的压缩前的文件夹
     *
     * @param file 删除的文件
     */
    public static void deleteFile(File file) {
        if (file.exists()) {                               // 判断文件是否存在
            if (file.isFile()) {                           // 判断是否是文件
                file.delete();
            } else if (file.isDirectory()) {               // 否则如果它是一个目录
                File files[] = file.listFiles();           // 声明目录下所有的文件 files[];
                for (int i = 0; i < files.length; i++) {   // 遍历目录下所有的文件
                    deleteFile(files[i]);                  // 把每个文件 用这个方法进行迭代
                }
            }
            file.delete();
        }
    }

    public static void main(String[] args) throws Exception {
        String targetFolderPath = "D:\\a";
        String newZipFilePath = "D:\\a.zip";

        //将目标目录的文件压缩成Zip文件
        ZipUtil.compress(targetFolderPath, newZipFilePath);
    }
}
```

**在controller处根据业务组装需要打包的文件夹：**  
下述controller代码实现的功能为，将同一期数下的不同子文本内容分为不同的文件夹，且将文本的对应的音频文件存放到对应的文本子文件夹中；同时，子文件夹同级存在一个总的统计excel（**使用了阿里的easyExcel包**）
```java
// 压缩文件临时生成地址
@Value("${file.temp.downUrl}")
private String tempDownUrl;

@GetMapping("/exportAudio")
@ApiOperation("数据审核 - 导出音频数据")
public void exportAudio(@RequestParam @Valid @NotEmpty(message = "期数id不能为空") @ApiParam(value = "期数id") String periodId, HttpServletResponse response) {
    try {
        // 生成excel到指定文件夹
        TbNumberPeriodsManagement tm = tbNumberPeriodsManagementService.getById(periodId);
        String zipParentUrl = tempDownUrl + "/" + tm.getNumber();
        File file = new File(zipParentUrl);// 不存在，创建
        if (!file.exists()) {
            file.mkdirs();
        }
        List<TbPeriodTextExcelResp> allList = recordingReviewService.allTextListByPeriodId(periodId);
        String fileName = URLEncoder.encode(tm.getNumber(), "UTF-8");
        EasyExcel.write(zipParentUrl + "/" + fileName + ".xlsx", TbPeriodTextExcelResp.class).sheet("sheet1").doWrite(allList);

        // 获取当前期数的所有录音文件（审核通过）
        List<TbRecordingReviewZipResp> fileList = recordingReviewService.allRecordingReviewListByPeriodId(periodId);
        for (TbRecordingReviewZipResp zipResp : fileList) {
            String zipAudioTextDir = zipParentUrl + "/" + zipResp.getTextNumber();
            File zipAudioTextDirFile = new File(zipAudioTextDir);// 不存在，创建
            if (!zipAudioTextDirFile.exists()) {
                zipAudioTextDirFile.mkdirs();
            }

            // 将音频文件按照不同的文本编号名字的文件夹名复制到指定文件夹
            String newFilePath = zipAudioTextDir + zipResp.getAudioFilePath().substring(zipResp.getAudioFilePath().lastIndexOf("/"));
            FileUtils.copyFile(new File(zipResp.getAudioFilePath()), new File(newFilePath));
        }

        // 打包压缩指定文件夹
        String zipDownLoadPath = tempDownUrl + "/" + tm.getNumber() + ".zip";
        ZipUtil.compress(zipParentUrl, zipDownLoadPath);

        // 下载
        InputStream inputStream = new FileInputStream(zipDownLoadPath);

        OutputStream outputStream = response.getOutputStream();
        response.setContentType("application/zip");
        response.addHeader("Content-Disposition", "attachment;filename=" + URLEncoder.encode(tm.getNumber() + ".zip", "UTF-8"));
        
        // 将字节从inputStream复制到outputStream流中
        IOUtils.copy(inputStream, outputStream);
        if (null != inputStream) {
            inputStream.close();
        }
        if (null != outputStream) {
            outputStream.close();
            outputStream.flush();
        }
    } catch (IOException e) {
        e.printStackTrace();
    }
}
```