package main

import (
	"bytes"
	"fmt"
	"text/template"

	"github.com/CloudyKit/jet"
	"github.com/flosch/pongo2"
	"github.com/hoisie/mustache"
	"github.com/valyala/fasttemplate"
)

var jetSet = jet.NewSet(jet.NewInMemLoader(), jet.WithSafeWriter(true))

// Mapping of available template engines
var TemplateEngines = map[string]func(string) (string, error){
	"go_text":    renderGoText,
	"mustache":   renderMustache,
	"fasttpl":    renderFastTemplate,
	"pongo2":     renderPongo2,
	"jet":        renderJet,
}

// Go text/template engine
func renderGoText(tpl string) (string, error) {
	t, err := template.New("tpl").Parse(tpl)
	if err != nil {
		return "", err
	}
	var buf bytes.Buffer
	err = t.Execute(&buf, map[string]interface{}{})
	return buf.String(), err
}

// Mustache
func renderMustache(tpl string) (string, error) {
	result := mustache.Render(tpl, map[string]interface{}{})
	return result, nil
}

// fasttemplate
func renderFastTemplate(tpl string) (string, error) {
	t := fasttemplate.New(tpl, "{{", "}}")
	result := t.ExecuteString(map[string]interface{}{})
	return result, nil
}

// Pongo2 (Jinja-like)
func renderPongo2(tpl string) (string, error) {
	t, err := pongo2.FromString(tpl)
	if err != nil {
		return "", err
	}
	out, err := t.Execute(map[string]interface{}{})
	return out, err
}

// Jet template
func renderJet(tpl string) (string, error) {
	name := fmt.Sprintf("tpl_%d.jet", len(tpl))
	err := jetSet.SetLoader(jet.NewInMemLoader().Set(name, tpl))
	if err != nil {
		return "", err
	}
	t, err := jetSet.GetTemplate(name)
	if err != nil {
		return "", err
	}
	var buf bytes.Buffer
	err = t.Execute(&buf, nil, nil)
	return buf.String(), err
}
