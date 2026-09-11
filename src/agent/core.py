import openai
import re
import requests
from src.agent.prompts import AGENT_SYSTEM_PROMPT

def google_search_tool(keyword: str) -> str:
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/v1/search?q={keyword}")
        if response.status_code == 200:
            data = response.json()
            return str(data.get("results", []))
    except Exception:
        pass
    return f"[Result for '{keyword}'] ข้อมูลจำลองจากระบบค้นหาสำรอง"

class AutonomousAgent:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        
    def execute_goal(self, user_goal: str) -> str:
        print(f"[Agent] เริ่มต้นทำงานเพื่อเป้าหมาย: {user_goal}")
        
        messages = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {user_goal}"}
        ]
        
        ai_thought = ""
        for loop in range(3):
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.2
            )
            
            ai_thought = response.choices[0].message.content
            print(f"\n--- [รอบที่ {loop + 1}] กระบวนการคิดของ AI ---")
            print(ai_thought)
            
            messages.append({"role": "assistant", "content": ai_thought})
            
            action_match = re.search(r'google_search_tool\(keyword="([^"]+)"\)', ai_thought)
            
            if action_match:
                search_keyword = action_match.group(1)
                print(f"[Agent Action] AI สั่งค้นหา Google ด้วยคีย์เวิร์ด: '{search_keyword}'")
                search_result = google_search_tool(search_keyword)
                messages.append({"role": "user", "content": f"Observation: {search_result}"})
            else:
                print("\n[Agent] ได้คำตอบสุดท้ายแล้ว จบการทำงาน")
                break
                
        return ai_thought
      
