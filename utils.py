import numpy as np
from rapidfuzz import fuzz


def is_one_line(bbox1, bbox2, y_thresh=2):
    top_1 = min(bbox1[0][1], bbox1[1][1])
    bot_1 = max(bbox1[2][1], bbox1[3][1])

    y1 = (bot_1 + top_1) / 2

    top_2 = min(bbox2[0][1], bbox2[1][1])
    bot_2 = max(bbox2[2][1], bbox2[3][1])

    y2 = (bot_2 + top_2) / 2

    if np.abs(y1 - y2) > y_thresh:
        return False

    return True


def is_next_value(bbox, values, y_thresh=5, x_thresh=5):
    # find most bottom values
    value = sorted(values, key=lambda x: x[0][3][1])[-1]
    bot = value[0][3][1]

    bbox_top = bbox[0][1]

    # print(bot, bbox_top)
    if np.abs(bbox_top - bot) > y_thresh:
        return False
    
    left = value[0][0][0]
    bbox_left = bbox[0][0]
    
    if np.abs(left - bbox_left) > x_thresh:
        return False

    return True


def has_key(bbox, keys):
    for key in keys:
        if is_one_line(key[0], bbox):
            return True

    return False


def merge_bbox(bbox1, bbox2):
    left = min([pt[0] for pt in bbox1] + [pt[0] for pt in bbox2])
    right = max([pt[0] for pt in bbox1] + [pt[0] for pt in bbox2])
    top = min([pt[1] for pt in bbox1] + [pt[1] for pt in bbox2])
    bot = max([pt[1] for pt in bbox1] + [pt[1] for pt in bbox2])

    return [[left, top], [right, top], [right, bot], [left, bot]]


def sort_result(result):
  return sorted(result, key=lambda x: x[0][0][0])


def merge_to_one_line(result):
    # merge result into one line
    merged_result = []
    done = []
    for i, row in enumerate(result):
        if i in done:
            continue
        merged = [row]
        for j, row2 in enumerate(result):
            if i != j and (i not in done) and (j not in done) and is_one_line(row[0], row2[0]):
                merged.append(row2)
                done.append(j)
        done.append(i)
        merged_result.append(merged)

    return merged_result


def find_keys_and_values(result, x_thresh=50):
    keys = []
    values = []
    for mer in result:
        mer = sort_result(mer)
        bbox = mer[0][0]
        x = bbox[1][0]
        text = []
        text2 = []
        bbox2 = []
        is_kv = False
        for row in mer:
            if row[0][0][0] - x > x_thresh:
                is_kv = True
                bbox2 = row[0]
            x = row[0][1][0]
            if not is_kv:
                bbox = merge_bbox(bbox, row[0])
                text.append(row[1])
            else:
                text2.append(row[1])
                bbox2 = merge_bbox(bbox2, row[0])
        if is_kv:
            keys.append((bbox, " ".join(text)))
            values.append((bbox2, " ".join(text2)))
        else:
            values.append((bbox, " ".join(text)))

    return keys, values

def find_value_from_key(result, key, thresh=80, x_thresh=50):
    merged_result = merge_to_one_line(result)
    keys, values = find_keys_and_values(merged_result, x_thresh=x_thresh)

    # find value
    value = []
    for k in keys:
        if fuzz.ratio(k[1], key) >= thresh:
            bbox = k[0]
            for row in values:
                if is_one_line(bbox, row[0]):
                    value.append(row)
                elif len(value) > 0 and is_next_value(row[0], value) and not has_key(row[0], keys):
                    value.append(row)
    return value

def combine_values(values, delimiter=' '):
  text = []
  for val in values:
    text.append(val[1])
  return f'{delimiter}'.join(text)