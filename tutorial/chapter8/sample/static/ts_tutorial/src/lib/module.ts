const TITLE: string = 'TypeScript入門';

export function showMessage(): void {
    console.log(`ようこそ ${TITLE}`);
}

export class Util {
    static getVersion(): string { return "1.0.0"; }
}