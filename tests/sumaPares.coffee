VAR suma = 0
VAR temp = 0
PRINT("Valor de n: ")
VAR n = INPUT_INT()
PRINT("Valor de m: ")
VAR m = INPUT_INT()

IF n > m THEN
	temp = n
	n = m
	m = temp
END

temp = n
WHILE temp <= m THEN
	IF temp % 2 == 0 THEN
		suma = suma + temp
	END
	temp = temp + 1
END

PRINT("La suma entre " + n + " y " + m + "es: " + suma)