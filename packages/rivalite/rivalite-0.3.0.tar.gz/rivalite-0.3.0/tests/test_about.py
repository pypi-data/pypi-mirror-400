from rivalite import about


modules = about()

print(str(modules)[1:-1])

for m in modules:
    print(f"=====[{m}]=====")
    print(about(m))
    input("Type enter to continue to the next module")

print("End of test")
