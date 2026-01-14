// Clean Go code without AI slop
package main

import "fmt"

func main() {
	x := 10
	fmt.Println("Value:", x)
	processData()
}

func processData() {
	data := []int{1, 2, 3}
	result := sum(data)
	fmt.Printf("Sum: %d\n", result)
}

func sum(data []int) int {
	total := 0
	for _, v := range data {
		total += v
	}
	return total
}
