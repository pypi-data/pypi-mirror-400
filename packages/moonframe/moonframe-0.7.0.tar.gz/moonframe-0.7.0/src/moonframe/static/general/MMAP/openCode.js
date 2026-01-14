const trustedPath = []

export function openCode(path, filename, lines = [0]) {

    if (!trustedPath.includes(path)) {
        const confirmed = window.confirm(
            `If you continue, VS Code will open a file from the repository: "${path}".\nIf you do not trust the path or if it seems incorrect, please modify the "mmap_in.yml" file directly before proceeding.`
        )

        if (confirmed) {
            window.location.href = `vscode://file//${path}/${filename}:${lines[0]}`
            trustedPath.push(path)
        }
    }
    else {
        window.location.href = `vscode://file//${path}/${filename}:${lines[0]}`
    }

}
