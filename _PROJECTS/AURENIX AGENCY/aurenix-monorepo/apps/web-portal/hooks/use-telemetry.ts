"use client"

import { useState, useEffect, useCallback } from "react"

export type TelemetryEvent = {
  session_id: string
  user_id: string
  task_type: string
  event_type: "started" | "completed" | "failed"
  message: string
  timestamp: string
  time_saved_ms?: number
}

export function useTelemetry(wsUrl: string = "ws://localhost:8000/ws/metrics") {
  const [events, setEvents] = useState<TelemetryEvent[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let ws: WebSocket | null = null
    let reconnectTimer: NodeJS.Timeout

    const connect = () => {
      try {
        ws = new WebSocket(wsUrl)

        ws.onopen = () => {
          console.log("Telemetry WebSocket Connected")
          setIsConnected(true)
          setError(null)
        }

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            const telemetryEvent: TelemetryEvent = {
              session_id: data.session_id,
              user_id: data.user_id,
              task_type: data.task_type,
              event_type: data.event_type || "info",
              message: data.message || `Task ${data.task_type} ${data.event_type}`,
              timestamp: new Date().toLocaleTimeString(),
              time_saved_ms: data.time_saved_ms
            }
            
            setEvents((prev) => [telemetryEvent, ...prev].slice(0, 10))
          } catch (e) {
            console.error("Error parsing telemetry message:", e)
          }
        }

        ws.onclose = () => {
          setIsConnected(false)
          console.log("Telemetry WebSocket Disconnected, retrying...")
          reconnectTimer = setTimeout(connect, 5000)
        }

        ws.onerror = (err) => {
          setError("WebSocket Connection Error")
          console.error("WebSocket Error:", err)
        }
      } catch (e) {
        setError("Failed to establish connection")
      }
    }

    connect()

    return () => {
      if (ws) ws.close()
      clearTimeout(reconnectTimer)
    }
  }, [wsUrl])

  return { events, isConnected, error }
}
