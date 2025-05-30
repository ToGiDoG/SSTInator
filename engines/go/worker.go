package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

func main() {
	fmt.Fprintln(os.Stderr, "🔄 Loading Go template engines...")

	enabled := map[string]bool{}
	if len(os.Args) > 1 {
		for _, name := range strings.Split(os.Args[1], ",") {
			enabled[strings.TrimSpace(name)] = true
		}
	}

	if len(enabled) == 0 {
		for name := range TemplateEngines {
			enabled[name] = true
		}
	}

	selected := []string{}
	for name := range enabled {
		if _, ok := TemplateEngines[name]; ok {
			selected = append(selected, name)
		}
	}

	fmt.Fprintf(os.Stderr, "✅ %d engine(s) ready: %s\n", len(selected), strings.Join(selected, ", "))

	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		tpl := scanner.Text()
		result := make(map[string]string)

		for name := range enabled {
			fn, ok := TemplateEngines[name]
			if !ok {
				result[name] = "❌ Unknown engine"
				continue
			}
			out, err := fn(tpl)
			if err != nil {
				result[name] = "❌ " + err.Error()
			} else {
				result[name] = out
			}
		}

		json.NewEncoder(os.Stdout).Encode(result)
		fmt.Println("__END__")
	}
}
