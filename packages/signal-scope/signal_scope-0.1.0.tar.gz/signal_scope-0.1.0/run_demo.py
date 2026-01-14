from signal_scope.core import analyze_ts

result = analyze_ts("demo.csv", col="value", plot=True)
print(result)
