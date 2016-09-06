def update_changed(obj, data, fields):
    changed_fields = []
    for key in fields:
        if getattr(obj, key) != data[key]:
            setattr(obj, key, data[key])
            changed_fields.append(key)

    if changed_fields:
        obj.save(update_fields=changed_fields)
