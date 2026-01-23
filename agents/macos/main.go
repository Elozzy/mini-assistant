package main

import (
	"mini-assistant/macos/tools"
	"net/http"

	"github.com/gin-gonic/gin"
)

type Action struct {
	Tool   string            `json:"tool"`
	Device string            `json:"device"`
	Args   map[string]string `json:"args"`
}

type AgentRequest struct {
	Actions []Action `json:"actions"`
}

func main() {
	r := gin.Default()

	// Health check
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	// Endpoint to execute actions
	r.POST("/execute", func(c *gin.Context) {
		var req AgentRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		results := make([]map[string]string, 0)

		for _, action := range req.Actions {
			res, err := tools.Execute(action.Tool, action.Args)
			status := "success"
			if err != nil {
				status = err.Error()
			}
			results = append(results, map[string]string{
				"tool":   action.Tool,
				"device": action.Device,
				"status": status,
				"output": res,
			})
		}

		c.JSON(http.StatusOK, gin.H{"results": results})
	})

	r.Run(":8081")
}
