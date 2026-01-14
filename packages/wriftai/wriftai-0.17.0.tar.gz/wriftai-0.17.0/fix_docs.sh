#!/bin/bash

if sed --version 2>/dev/null | head -1 | grep -q "GNU"; then
    SED_ARGS=(-i)
    echo "Detected GNU sed (Linux)"
else
    SED_ARGS=(-i '')
    echo "Detected BSD sed (macOS)"
fi

find docs/reference -name "*.md" -type f -exec sed "${SED_ARGS[@]}" \
    -e 's/(\*list\* \*\[\*\*JsonValue\* \*\]\*  \*|\* \*Mapping\* \*\[\*\*str\* \*,\* \*JsonValue\* \*\]\*  \*|\* \*str\* \*|\* \*bool\* \*|\* \*int\* \*|\* \*float\* \*|\* \*None\*)/(*Optional[JsonValue]*)/g' \
    -e 's/list\[JsonValue\] | \*Mapping\*\[str, JsonValue\] | str | bool | int | float | None/JsonValue/g' \
    -e 's/(\*list\* \*\[\*\*T\* \*\]\*)/(*list*[*T*])/g' \
    -e 's/(\*dict\* \*\[\*\*str\* \*,\* \*Any\* \*\]\*  \*|\* \*None\*)/(*Optional[dict[str, Any]]*)/g' \
    -e 's/(\*Mapping\* \*\[\*\*str\* \*,\* \*Any\* \*\]\*  \*|\* \*None\*)/(*Optional[Mapping[str, Any]]*)/g' \
    -e 's/\*\[\*\*None\* \*\]\* \*\]\*/\*\[\*\*None\*\*\]\* \*\]\*/g' \
    {} \;

echo "Fixed docs!"