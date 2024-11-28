export interface Channel {
    id: string
    name: string
    type: number
    position?: number
}

export interface Summary {
    text: string;
    timestamp: string;
    channelName: string;
}