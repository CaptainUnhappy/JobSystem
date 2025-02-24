import json
import datetime, time
from utils.config import DB_CONFIG
import asyncio
import aiohttp
import aiomysql
from typing import Optional
import random
from asyncio import Semaphore

# 全局设置
MAX_CONCURRENT_REQUESTS = 10  # 最大并发请求数
RETRY_TIMES = 3  # 最大重试次数
MIN_DELAY = 0.5  # 最小延迟时间(秒)
MAX_DELAY = 1.5  # 最大延迟时间(秒)

# 创建数据库连接池
async def create_pool():
    return await aiomysql.create_pool(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        db=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
        autocommit=True,
        maxsize=20,  # 增加连接池大小
        minsize=5,   # 设置最小连接数
        pool_recycle=3600  # 连接回收时间
    )

# 异步获取页面数据
async def get_page_data(url: str, session: aiohttp.ClientSession, semaphore: Semaphore) -> Optional[str]:
    async with semaphore:  # 使用信号量控制并发
        for attempt in range(RETRY_TIMES):
            try:
                # 添加随机延迟
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                await asyncio.sleep(delay)
                
                async with session.get(url, timeout=10) as response:  # 添加超时设置
                    if response.status == 429:  # Too Many Requests
                        wait_time = random.uniform(1, 3)
                        print(f"请求过多，等待 {wait_time:.2f} 秒后重试: {url}")
                        await asyncio.sleep(wait_time)
                        continue
                    elif response.status != 200:
                        print(f"获取页面失败: {url}, 状态码: {response.status}")
                        if attempt < RETRY_TIMES - 1:
                            continue
                        return None
                    return await response.text()
            except asyncio.TimeoutError:
                print(f"请求超时: {url}")
                if attempt < RETRY_TIMES - 1:
                    continue
                return None
            except Exception as e:
                print(f"请求异常: {url}, 错误: {e}")
                if attempt < RETRY_TIMES - 1:
                    continue
                return None
    return None

# 异步保存数据
async def save_data(pool, job_data: dict, category: str):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # 使用事务
                await conn.begin()
                
                # 检查是否已存在
                check_sql = """
                    SELECT job_id FROM jobs_info 
                    WHERE job_name = %s AND area = %s AND company_name = %s
                    LIMIT 1
                """
                await cursor.execute(check_sql, (
                    job_data['job_name'],
                    job_data['area'],
                    job_data['company_name']
                ))
                exists = await cursor.fetchone()
                
                if not exists:
                    # 插入新数据
                    insert_sql = """
                        INSERT INTO jobs_info(
                            job_id, job_name, salary, degree, categories, major, 
                            welfare, head_count, publish_date, update_date, source,
                            company_name, area, company_scale, company_property
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """
                    await cursor.execute(insert_sql, (
                        str(job_data['job_id']),
                        str(job_data['job_name']),
                        int(job_data['salary']),
                        str(job_data['degree']),
                        str(category),
                        str(job_data['major'])[:500],
                        str(job_data['welfare']),
                        str(job_data['head_count']),
                        str(job_data['publish_date']),
                        str(job_data['update_date']),
                        str(job_data['source']),
                        str(job_data['company_name']),
                        str(job_data['area']),
                        str(job_data['company_scale']),
                        str(job_data['company_property'])
                    ))
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                print(f"数据库操作失败: {e}")
                print(f"问题数据: {job_data}")

# 处理职位数据
async def process_jobs(data: str, category: str, pool) -> None:
    try:
        json_data = json.loads(data)
        jobs = json_data["data"]["list"]
        
        tasks = []
        for job in jobs:
            # 构建职位数据
            job_data = {
                'job_id': job["jobId"],
                'job_name': job["jobName"],
                'salary': int(job["lowMonthPay"]) * 1000,
                'degree': job["degreeName"],
                'major': job["major"] or "",
                'welfare': job["recTags"] or "",
                'head_count': job["headCount"],
                'source': job["sourcesNameCh"] or "大学生就业服务平台",
                'company_name': job["recName"],
                'area': job["areaCodeName"],
                'company_scale': job["recScale"] or "",
                'company_property': job["recProperty"],
                'publish_date': time.strftime("%Y-%m-%d", time.localtime(int(job["publishDate"] / 1000))),
                'update_date': time.strftime("%Y-%m-%d", time.localtime(int(job["updateDate"] / 1000)))
            }
            
            # 跳过无效数据
            if job_data['salary'] == 0 or job_data['head_count'] == '':
                continue
                
            # 异步保存数据
            task = asyncio.create_task(save_data(pool, job_data, category))
            tasks.append(task)
            
        if tasks:
            await asyncio.gather(*tasks)
            
    except Exception as e:
        print(f"数据处理失败: {e}")

async def main():
    # 职位类别
    categories = {
        '01': '计算机/网络/技术类',
        '02': '电子/电器/通信技术类',
        '03': '行政/后勤类',
        '04': '翻译类',
        '05': '销售类',
        '06': '客户服务类',
        '07': '市场/公关/媒介类',
        '08': '咨询/顾问类',
        '09': '技工类',
        '10': '财务/审计/统计类',
        '11': '人力资源类',
        '12': '教育/培训类',
        '13': '质量管理类',
        '14': '美术/设计/创意类',
        '15': '金融保险类',
        '16': '贸易/物流/采购/运输类',
        '17': '经营管理类',
        '18': '商业零售类',
        '19': '建筑/房地产/装饰装修/物业管理类',
        '20': '法律类',
        '21': '酒店/餐饮/旅游/服务类',
        '22': '生物/制药/化工/环保类',
        '23': '文体/影视/写作/媒体类',
        '24': '机械/仪器仪表类',
        '25': '科研类',
        '26': '工厂生产类',
        '27': '医疗卫生/美容保健类',
        '28': '电气/能源/动力类',
        '29': '其他类'
    }

    # 创建数据库连接池
    pool = await create_pool()
    
    # 创建信号量
    semaphore = Semaphore(MAX_CONCURRENT_REQUESTS)
    
    # 自定义 aiohttp 会话配置
    timeout = aiohttp.ClientTimeout(total=30)
    conn = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS, force_close=True)
    
    # 创建 aiohttp 会话
    async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
        tasks = []
        
        # 创建所有任务
        for index in range(1, 30):
            ind = f"{index:02d}"
            tasks = []  # 存储每个类别的任务
            timeout_urls = []  # 存储请求超时的URL
            
            # 并发获取每个类别下的1-10页数据
            for page in range(1, 11):
                url = f"https://www.ncss.cn/student/jobs/jobslist/ajax/?&limit=20&offset={page}&categoryCode={ind}"
                
                # 获取页面数据
                print(f"正在处理: 类别 {ind} 第 {page} 页")
                task = asyncio.create_task(get_page_data(url, session, semaphore))
                tasks.append(task)
            
            # 等待所有任务完成
            data_list = await asyncio.gather(*tasks)
            
            # 处理每个页面的数据
            for data in data_list:
                if data and '"list":[],' not in data:
                    # 处理职位数据
                    task = asyncio.create_task(
                        process_jobs(data, categories[ind], pool)
                    )
                    tasks.append(task)
                elif data is None:  # 如果数据为None，表示请求超时
                    timeout_urls.append(url)  # 收集超时的URL
            
            # 等待所有职位处理任务完成
            if tasks:
                await asyncio.gather(*tasks)

        # 统一重新获取超时的URL数据
        if timeout_urls:
            print(f"重新获取超时的URL: {timeout_urls}")
            retry_tasks = [asyncio.create_task(get_page_data(url, session, semaphore)) for url in timeout_urls]
            retry_data_list = await asyncio.gather(*retry_tasks)
            
            # 处理重新获取的数据
            for data in retry_data_list:
                if data and '"list":[],' not in data:
                    # 处理职位数据
                    ind = ...  # 需要根据URL或其他信息确定类别
                    task = asyncio.create_task(
                        process_jobs(data, categories[ind], pool)
                    )
                    tasks.append(task)
            
            # 等待所有重新处理的职位任务完成
            if tasks:
                await asyncio.gather(*tasks)
    
    # 关闭连接池
    pool.close()
    await pool.wait_closed()

if __name__ == '__main__':
    start_time = time.time()
    
    # 设置更大的并发限制
    import platform
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
    
    end_time = time.time()
    print(f"总耗时: {end_time - start_time:.2f} 秒")
