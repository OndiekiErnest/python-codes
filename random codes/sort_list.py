# sort list based on a custom key

def last_name_key(name: str):
    # split the name string on space
    names = name.split()
    # names = ["name"]
    if len(names) > 1:
        # return second name
        return names[1]
    # else return only name
    return name


def sort(lst: list):
    """ sort based on custom key """
    # use custom key
    sort_key = last_name_key
    # sort the list using the key
    lst.sort(key=sort_key)
    # return the list
    return lst


if __name__ == "__main__":

    sortd = sort(["you", "name cd", "name ab willy", "name"])
    print(sortd)

    # lst = [9, "name", 3.0]
    # for item in lst:
    #     print("\t", len(item))
