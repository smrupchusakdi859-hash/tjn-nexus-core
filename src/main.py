import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="TJN-NEXUS-CORE API Gateway",
    version="1.0.0",
    description="Core API Gateway for Master 01 Autonomous & Hardware Bridge System"
)

class SystemStatus(BaseModel):
    status: str
    master_id: str
    secure_ip: str
    hardware_port: str
    frequency_hz: float

@app.get("/")
def read_root():
    return {
        "system": "TJN-NEXUS-CORE",
        "authority": "Supreme Authority - Master 01",
        "state": "ONLINE"
    }

@app.get("/health", response_model=SystemStatus)
def health_check():
    return SystemStatus(
        status="HEALTHY",
        master_id="TJN-M01-000001",
        secure_ip=os.getenv("SECURE_TUNNEL_IP", "100.89.244.3"),
        hardware_port=os.getenv("HARDWARE_PORT", "COM3"),
        frequency_hz=float(os.getenv("FREQUENCY_HZ", 528.45))
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8888))
    uvicorn.run(app, host="0.0.0.0", port=port)version: '3.8'

# ==============================================================
#  TJN NEXUS CORE - PRODUCTION DEPLOYMENT BLUEPRINT
#  Master Authority: TJN-M01-000001 (ชูศักดิ์ สมรูป)
#  System Version: v58.0.3_FINAL
# ==============================================================

name: tjn-nexus-core-production

networks:
  nexus_secure_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16

volumes:
  nexus_data_store:
    driver: local
  nexus_logs:
    driver: local

services:
  api_gateway:
    image: python:3.11-slim
    container_name: tjn_api_gateway
    restart: always
    working_dir: /app
    volumes:
      - .:/app
      - nexus_data_store:/app/data
      - nexus_logs:/app/logs
    environment:
      - ENVIRONMENT=production
      - PORT=8888
      - SECURE_TUNNEL_IP=100.89.244.3
      - HARDWARE_PORT=COM3
      - FREQUENCY_HZ=528.45
      - MASTER_ID=TJN-M01-000001
    ports:
      - "8888:8888"
    networks:
      - nexus_secure_net
    command: >
      sh -c "pip install --no-cache-dir -r requirements.txt &&
             python -u src/main.py"
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8888/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s

  autopilot_keeper:
    image: python:3.11-slim
    container_name: tjn_autopilot_keeper
    restart: always
    working_dir: /app
    volumes:
      - .:/app
      - nexus_logs:/app/logs
    environment:
      - KEEP_ALIVE_INTERVAL=60
      - SYSTEM_MODE=AUTONOMOUS
      - MASTER_ID=TJN-M01-000001
    networks:
      - nexus_secure_net
    command: python -u autopilot_keeper.py
    depends_on:
      - api_gateway

  master_bridge:
    image: python:3.11-slim
    container_name: tjn_master_bridge
    restart: always
    working_dir: /app
    volumes:
      - .:/app
    environment:
      - MASTER_ID=TJN-M01-000001
      - SECURE_GATEWAY=ACTIVE
      - ORCID=0009-0001-9791-2860
    networks:
      - nexus_secure_net
    command: python -u tjn_master_bridge.py
    depends_on:
      - api_gateway
