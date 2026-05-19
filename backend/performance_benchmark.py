import asyncio
import time
import statistics
from typing import List, Dict
import httpx
import os


class PerformanceBenchmark:
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.results: Dict[str, List[float]] = {}
    
    async def measure_ocr_time(self, pdf_path: str) -> float:
        if not os.path.exists(pdf_path):
            print(f"测试文件不存在: {pdf_path}")
            return 0.0
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(pdf_path, "rb") as f:
                files = {"file": (os.path.basename(pdf_path), f, "application/pdf")}
                
                start_time = time.time()
                response = await client.post(f"{self.base_url}/ocr", files=files)
                end_time = time.time()
                
                if response.status_code != 200:
                    print(f"OCR请求失败: {response.status_code} - {response.text}")
                    return 0.0
                
                return end_time - start_time
    
    async def measure_suggestions_time(self, resume_id: int, style_type: str = "", target_job: str = "") -> float:
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {"resumeId": resume_id, "styleType": style_type, "targetJob": target_job}
            
            start_time = time.time()
            response = await client.post(f"{self.base_url}/suggestions", json=payload)
            end_time = time.time()
            
            if response.status_code != 200:
                print(f"建议生成请求失败: {response.status_code} - {response.text}")
                return 0.0
            
            return end_time - start_time
    
    async def run_benchmark(self, pdf_path: str, iterations: int = 5):
        print(f"\n{'='*60}")
        print(f"性能基准测试")
        print(f"测试文件: {pdf_path}")
        print(f"迭代次数: {iterations}")
        print(f"{'='*60}\n")
        
        ocr_times = []
        suggestion_times = []
        total_times = []
        
        for i in range(iterations):
            print(f"第 {i+1}/{iterations} 次测试...")
            
            ocr_time = await self.measure_ocr_time(pdf_path)
            if ocr_time > 0:
                ocr_times.append(ocr_time)
                print(f"  OCR时间: {ocr_time:.2f}秒")
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{self.base_url}/resumes")
                    resumes = response.json()
                    if resumes:
                        resume_id = resumes[0]["resumeId"]
                        
                        suggestion_time = await self.measure_suggestions_time(resume_id)
                        if suggestion_time > 0:
                            suggestion_times.append(suggestion_time)
                            print(f"  建议生成时间: {suggestion_time:.2f}秒")
                            
                            total_times.append(ocr_time + suggestion_time)
            
            await asyncio.sleep(1)
        
        print(f"\n{'='*60}")
        print("测试结果统计")
        print(f"{'='*60}\n")
        
        if ocr_times:
            print("OCR处理时间:")
            print(f"  平均: {statistics.mean(ocr_times):.2f}秒")
            print(f"  最小: {min(ocr_times):.2f}秒")
            print(f"  最大: {max(ocr_times):.2f}秒")
            print(f"  中位数: {statistics.median(ocr_times):.2f}秒")
            if len(ocr_times) > 1:
                print(f"  标准差: {statistics.stdev(ocr_times):.2f}秒")
        
        if suggestion_times:
            print("\n建议生成时间:")
            print(f"  平均: {statistics.mean(suggestion_times):.2f}秒")
            print(f"  最小: {min(suggestion_times):.2f}秒")
            print(f"  最大: {max(suggestion_times):.2f}秒")
            print(f"  中位数: {statistics.median(suggestion_times):.2f}秒")
            if len(suggestion_times) > 1:
                print(f"  标准差: {statistics.stdev(suggestion_times):.2f}秒")
        
        if total_times:
            print("\n总处理时间:")
            print(f"  平均: {statistics.mean(total_times):.2f}秒")
            print(f"  最小: {min(total_times):.2f}秒")
            print(f"  最大: {max(total_times):.2f}秒")
            print(f"  中位数: {statistics.median(total_times):.2f}秒")
            print(f"  95分位: {sorted(total_times)[int(len(total_times) * 0.95)] if len(total_times) > 1 else total_times[0]:.2f}秒")
        
        print(f"\n{'='*60}")
        
        return {
            "ocr_times": ocr_times,
            "suggestion_times": suggestion_times,
            "total_times": total_times,
        }
    
    async def get_performance_stats(self) -> Dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/performance/stats")
            return response.json()


async def main():
    benchmark = PerformanceBenchmark()
    
    test_pdf = "test_resume.pdf"
    if not os.path.exists(test_pdf):
        print(f"请提供测试PDF文件: {test_pdf}")
        print("或者修改脚本中的 test_pdf 变量指向实际的PDF文件")
        return
    
    results = await benchmark.run_benchmark(test_pdf, iterations=5)
    
    print("\n\n服务器端性能统计:")
    stats = await benchmark.get_performance_stats()
    for operation, data in stats.items():
        if data["count"] > 0:
            print(f"\n{operation}:")
            print(f"  平均: {data['avg']:.2f}秒")
            print(f"  最小: {data['min']:.2f}秒")
            print(f"  最大: {data['max']:.2f}秒")
            print(f"  次数: {data['count']}")


if __name__ == "__main__":
    asyncio.run(main())
