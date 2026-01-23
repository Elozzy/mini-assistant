package tools

import (
	"fmt"
	"os/exec"
)

func Execute(tool string, args map[string]string) (string, error) {
	switch tool {
	case "apps.open":
		appName := args["app_name"]
		if appName == "" {
			return "", fmt.Errorf("app_name is required")
		}
		cmd := exec.Command("open", "-a", appName)
		err := cmd.Run()
		if err != nil {
			return "", err
		}
		return fmt.Sprintf("%s opened successfully", appName), nil

	case "filesystem.search":
		// Example: only search Desktop for now
		extension := args["extension"]
		if extension == "" {
			extension = "*"
		}
		cmd := exec.Command("find", "~/Desktop", "-name", fmt.Sprintf("*.%s", extension))
		output, err := cmd.CombinedOutput()
		if err != nil {
			return "", err
		}
		return string(output), nil

	case "system.info":
		cmd := exec.Command("sw_vers")
		output, err := cmd.CombinedOutput()
		if err != nil {
			return "", err
		}
		return string(output), nil

	default:
		return "", fmt.Errorf("tool %s not implemented", tool)
	}
}
