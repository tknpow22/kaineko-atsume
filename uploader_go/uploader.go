package main

import (
	"html/template"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"fmt"
)

func uploadHandler(w http.ResponseWriter, r *http.Request) {

	uploadfrom := ""
	result := "failure"

	for r.Method == "POST" {
		uploadfrom = r.PostFormValue("uploadfrom")

		if uploadfrom != "" {

			uploadFile, handler, err := r.FormFile("picture")
			if err != nil {
				fmt.Println(err)
				break
			}
			defer uploadFile.Close()

			filename := filepath.Base(handler.Filename)

			saveFile, err := os.Create("files/" + filename)
			if err != nil {
				fmt.Println(err)
				break
			}
			defer saveFile.Close()

			io.Copy(saveFile, uploadFile)
			result = "success"

			fmt.Println("upload:", filename)
		}

		break
	}

	if uploadfrom == "take_picture" {
		fmt.Fprintf(w, result)
	} else {
		http.Redirect(w, r, "/uploadpage", http.StatusFound)
	}
}

func uploadPageHandler(w http.ResponseWriter, r *http.Request) {
	var templ = template.Must(template.ParseFiles("uploadpage.html"))
	templ.Execute(w, "uploadpage.html")
}

func main() {
	http.HandleFunc("/uploadpage", uploadPageHandler)
	http.HandleFunc("/upload", uploadHandler)

	http.ListenAndServe("0.0.0.0:8080", nil)
}
